defmodule StringMatching.Sharder do
  @moduledoc"""
  Sharder of StringMatching processes, the Sharder contact 
  StringMatching Servers that exist in the Regsitry via 
  GenServer
  """
  @behaviour StringMatching.Sharder.Interface.Behaviour
  use GenServer
  require Logger
  alias StringMatching.Server.Interface, as: Worker
  alias StringMatching.Metadata, as: Agent
  @name __MODULE__
  @registry StringMatching.Servers.Registry
  @supervisor StringMatching.Dsupervisor
  
  @doc """
  API: Start the sharder
  """
  def start_link(_arg),
    do: GenServer.start_link(__MODULE__, :ok, name: @name)

  @doc """
  Init the sharder
  """
  def init(:ok),
    do: {:ok, %{}}

  @doc """
  API: stop the sharder
  """
  def stop(name), do: GenServer.stop(@name)
 
  @doc """
  API: crash
  """
  def crash(name), do: GenServer.cast(@name, :raise)

  @doc """
  API: feed all StringMatching automaton with patterns, it resets
  the workers
  """
  def dispatch_patterns(patterns),
    do: GenServer.cast(@name, {:local_dispatch, patterns})
  
  @doc """
  API: feed a specific StringMatching automaton with patterns, 
  it resets that worker
  """
  def dispatch_patterns(patterns, worker_name),
    do: GenServer.cast(@name, {:local_dispatch, patterns, worker_name})

  @doc """
  API: perform a pattern search
  """
  def fully_search(string),
    do: GenServer.call(@name, {:search, string})

  @doc """
  Callback to handle feeding specific needles state
  """
  def handle_cast({:local_dispatch, patterns, worker_name}, _state) do
    Logger.info("Refeeding automatons #{worker_name}")
    Worker.update(worker_name, patterns);
    Agent.add_patterns(worker_name, patterns)
    {:noreply, patterns}
  end

  @doc """
  Callback to handle feeding the automatons, Sharding algorithm to be
  reviewed
  """
  def handle_cast({:local_dispatch, pattern}, _state) when is_binary(pattern) do
    length = String.length(pattern)
    # Get the smallest shard of a specific length
    smallest_shard_name = @supervisor
    |> get_smallest_shard(length)
    Logger.info("Adding '#{pattern}' to #{smallest_shard_name}")
    # Update workers
    Worker.update(smallest_shard_name, pattern);
    # Update Server metadata
    Agent.add_patterns(smallest_shard_name, pattern)
    {:noreply, pattern}
  end

  @doc """
  Callback to handle feeding the automatons, Sharding algorithm to be
  reviewed
  """
  def handle_cast({:local_dispatch, patterns}, _state) do
    Logger.info("Sharding...")
    # Group patterns by length and prepare them to be sharded
    patterns
    |> Helpers.Hash.groupby_length
    # Balance shards
    |> Enum.each(fn {x, y} ->
      {min_size, _} = get_smallest_sizes(@supervisor, x)
      (fn -> rebalance(y, min_size, x) end).()
      # Update each shard
      |> Enum.each(fn {{_, worker_name}, x} ->
        Worker.update(worker_name, x)
        Agent.add_patterns(worker_name, x) end)
    end)
    {:noreply, patterns}
  end

  @doc """
  Callback to handle search using all automatons
  """
  def handle_call({:search, string}, _from, state) do
    results = @supervisor
    |> Helpers.ProcessesGetter.get_workers(:not_empty)
    |> Task.async_stream(fn x -> Worker.search(x, string) end)
    |> Enum.map(fn({:ok, result}) -> result end)
    # Flatting the results from multiple local workers
    |> Enum.flat_map(fn x -> x end)
    {:reply, results, state}
  end

  # Resharding, the alogirthm used in this founction:
  # 1 - We take the size of the smallest shard (min_size)
  # 2 - We take the n last needle of each shard whose size in S
  # where n = S - min_size
  # 3 - Concatenate the results of second step in a list
  # 4 - rechunk the list from step 4 uniformally to all shards
  def rebalance(patterns_list, min_size, length) do
    # Get server of a specific length
    workers = Helpers.ProcessesGetter.get_agents(@supervisor)
    |> Enum.map(fn x -> {Agent.get(:length, x), x} end)
    |> Enum.filter(fn {l, name} -> l == length end)
    # Take the last n elements of each needles and concatenate the
    # results in a new list
    redis_list = workers |> Enum.reduce([], fn {_len, worker}, acc ->
      Agent.get(:patterns, worker)
      |> Enum.take(min_size - Agent.get(:size, worker))
      |> Enum.concat(acc) end)
    # Remove `to be redistributed list` from workers
    Enum.each(
      workers, fn {l, name} ->
	Worker.remove(name, redis_list)
	Agent.remove_patterns(name, redis_list)
      end)
    # Concatenate all the last elements with 
    new_patterns = redis_list |> Enum.concat(patterns_list)
    # workers count
    workers_count = length(workers)
    # Chunk patterns into rebalanced workers
    every = new_patterns
    |> Enum.count
    |> Kernel./(workers_count)
    |> ceil
    sub_patterns = new_patterns |> Enum.chunk_every(every)
    Enum.zip(workers, sub_patterns) |> Enum.into(%{})
  end

  defp get_smallest_shard(supervisor_id, length) do
    Helpers.ProcessesGetter.get_agents(supervisor_id)
    |> Enum.map(fn x -> {Agent.get(:length,x), x} end)
    |> Enum.filter(fn {l, name} -> l == length end)
    |> Enum.map(fn {_l, name} -> {Agent.get(:size,name), name} end)
    |> Enum.min
    |> (fn {_, worker_name} -> worker_name end).()
  end
  
  # Get the first and the second smallest workers of a certain size
  def get_smallest_sizes(supervisor_id, pattern_length) do
    local_workers = Helpers.ProcessesGetter.get_agents(supervisor_id)
    length_workers = local_workers
    |> Enum.filter(fn x -> Agent.get(:length, x) == pattern_length end)
    |> Enum.map(fn x -> Agent.get(:size, x) end)
    |> Enum.sort |> Enum.uniq
    |> Enum.take(2) |> List.to_tuple
    |> (fn
      {x1, x2} -> {x1, x2}
      {x1} -> {x1, x1}
      {} -> {0,0} end).()
  end

  # Get total number of patterns by length in the node
  def count_patterns_bylength(supervisor_id, length) do
    local_workers = Helpers.ProcessesGetter.get_agents(supervisor_id)
    |> Enum.filter(fn x -> Agent.get(:length, x) == length end)
    |> Enum.reduce(0, fn x, acc -> Agent.get(:size, x) + acc end)
  end
  
  # Check if a pattern is a member of worker node (all workers under
  # this node)
  def is_there(pattern) when is_binary(pattern) do
    pattern_length = String.length(pattern)
    exists = fn x ->
      Agent.get(:patterns, x)
      |> MapSet.member?(pattern)
    end
    Node.Servers.get
    |> Map.get(pattern_length, [])
    |> Enum.any?(exists)
  end
end
