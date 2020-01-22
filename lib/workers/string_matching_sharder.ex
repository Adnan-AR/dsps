defmodule StringMatching.Sharder do
  @moduledoc"""
  Sharder of StringMatching processes, the Sharder contact 
  StringMatching Servers that exist in the Regsitry via 
  GenServer
  """
  use GenServer
  require Logger
  alias StringMatching.Server.Interface, as: Worker
  alias StringMatching.Metadata, as: Agent
  alias Node.Metadata, as: MetaAgent
  @name __MODULE__
  @registry StringMatching.Servers.Registry
  @supervisor StringMatching.Dsupervisor
  
  @doc """
  Start the sharder
  """
  def start_link(_arg),
    do: GenServer.start_link(__MODULE__, :ok, name: @name)

  @doc """
  Init the sharder
  """
  def init(:ok),
    do: {:ok, %{}}

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
  Callback to handle feeding specific automaton
  """
  def handle_cast({:local_dispatch, patterns, worker_name}, _state) do
    Logger.info("Refeeding automatons #{worker_name}")
    Worker.update(worker_name, patterns);
    MetaAgent.add_patterns(patterns);
    Agent.set(worker_name,
      {patterns, length(patterns), Enum.take(patterns, -1)})
    {:noreply, patterns}
  end

  @doc """
  Callback to handle feeding the automatons, Sharding algorithm to be
  reviewed
  """
  def handle_cast({:local_dispatch, pattern}, _state) when is_binary(pattern) do
    # Get the smallest shard
    smallest_shard_name = get_smallest_shard(@supervisor)
    Logger.info("Adding '#{pattern}' to #{smallest_shard_name}")
    # Get existing patterns
    new_patterns = Agent.get(:patterns, smallest_shard_name)
    |> Enum.concat([pattern])
    # Update workers
    # Worker.update(smallest_shard_name, new_patterns);
    Worker.update(smallest_shard_name, pattern);
    # Update Node Metadata
    MetaAgent.add_patterns(pattern)
    # Modify the metadata of the worker (modify the agent)
    # last_pattern = Enum.take(pattern, -1)
    # size_patterns = Enum.count(new_patterns)
    size_patterns = Agent.get(:size, smallest_shard_name) + 1
    Agent.set(
      # smallest_shard_name,{new_patterns, size_patterns, last_pattern})
      smallest_shard_name,{new_patterns, size_patterns, pattern})
    {:noreply, pattern}
    # {:noreply, new_patterns}
  end

  @doc """
  Callback to handle feeding the automatons, Sharding algorithm to be
  reviewed
  """
  def handle_cast({:local_dispatch, patterns}, _state) do
    Logger.info("Refeeding smallest automatons")
    patterns
    |> chunk_patterns
    |> Enum.each(fn {worker_name, x} ->
      Worker.update(worker_name,x);
      Agent.set(worker_name, {x, length(x), Enum.take(x, -1)})
    end)
    MetaAgent.add_patterns(patterns)
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

  # Chunck a list
  defp chunk_patterns(patterns_list) do
    workers_count = @registry |> Registry.count
    workers = @supervisor |> Helpers.ProcessesGetter.get_workers
    every = patterns_list
    |> Enum.count
    |> Kernel./(workers_count)
    |> ceil
    sub_patterns = patterns_list |> Enum.chunk_every(every)
    Enum.zip(workers, sub_patterns) |> Enum.into(%{})
  end

  # Chunck a list
  def chunk_patterns_rabin(patterns_list, min_sizes, length) do    
    # Get the difference between the sizes of the 
    diff = fn
      {x, y} -> y - x
      {_} -> 0 end
    size_diff = diff.(min_sizes)
    # Get smallest workers (by size not by length)
    workers = @supervisor |> get_smallest_shards(length)
    workers_count = length(workers)
    every = patterns_list
    |> Enum.count
    |> Kernel./(workers_count)
    |> ceil
    sub_patterns = patterns_list |> Enum.chunk_every(every)
    Enum.zip(workers, sub_patterns) |> Enum.into(%{})
  end

  defp get_smallest_shard(supervisor_id) do
    Helpers.ProcessesGetter.get_agents(supervisor_id)
    |> Enum.map(fn x -> {Agent.get(:size,x), x} end)
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
  end
  
  def get_smallest_shards(supervisor_id, pattern_length) do
    local_workers = Helpers.ProcessesGetter.get_agents(supervisor_id)
    length_workers = local_workers
    |> Enum.map(fn x -> {Agent.get(:length, x), x} end)
    # TODO: optimize (smallest workers of a certain pattern size)
    smallest_size = length_workers
    |> Enum.filter(fn {y, x} -> y == pattern_length end)
    |> Enum.map(fn {y, x} -> Agent.get(:size, x) end)
    |> Enum.min
    length_workers
    |> Enum.filter(fn  {y, x} ->  y == pattern_length end)
  end

  # Check if a pattern is a member of worker node (all workers under
  # this node)
  def is_there(pattern) do
    exists = fn x -> Agent.get(:patterns, x)
      |> Enum.member?(pattern)
    end
    Helpers.ProcessesGetter.get_agents(@supervisor)
    |> Enum.any?(exists)
  end

  # check the minimum of couple (used in chunking)
  defp min_tuple({x, y}) when x > y, do: y
  defp min_tuple({x, y}), do: x
  defp min_tuple({x}), do: nil
end
