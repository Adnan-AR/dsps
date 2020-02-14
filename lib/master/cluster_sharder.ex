defmodule Cluster.Sharder do
  @moduledoc"""
  Sharder of StringMatching processes, the Sharder contact 
  StringMatching Servers that exist in the Regsitry via 
  GenServer
  """
  use GenServer
  require Logger
  alias Node.Servers, as: MetaAgent
  alias StringMatching.Sharder, as: LocalSharder
  alias StringMatching.Dsupervisor, as: Supervisor
  
  @doc """
  Start the orcherstrer
  """
  def start_link(name),
    do: GenServer.start_link(__MODULE__, :ok, name: via(name))

  @doc """
  Init the Orcherstrer
  """
  def init(name),
    do: {:ok, name}

  @doc """
  API (recursive): Shard a list of patterns across the cluster
  """
  def dispatch_patterns(patterns, name) do
    GenServer.cast(via(name), {:global_dispatch, patterns})
  end
  
  @doc """
  Callback to add a single pattern to the cluster
  """
  def handle_cast({:global_dispatch, pattern}, _state)
  when is_binary(pattern) do
    pattern_l = String.length(pattern)
    workers = Helpers.ProcessesGetter.get_workers(:fetch_config)
    if is_incluster(pattern, pattern_l) do
      try do
	raise AlreadyExistError, pattern
      rescue
   	e in AlreadyExistError -> IO.inspect(e)
      end
    else
      # adding pattern to the register
      register_patterns(pattern, pattern_l)
      # adding pattern to worker
      pattern_l
      |> get_smallest_worker
      |> :rpc.call(
	StringMatching.Sharder, :dispatch_patterns, [pattern])
    end
    {:noreply, pattern}
  end
  @doc """
  Callback to feed all nodes across cluster with patterns
  """
  def handle_cast({:global_dispatch, pattern}, _state) do
    # Connected workers
    workers = Helpers.ProcessesGetter.get_workers(:fetch_config)
    # Filter already existed patterns
    pattern = filter_registered(pattern)
    # Starting Python process
    {:ok, pid_python} = :python.start(
      [{:python_path, 'lib/master'}, {:python, 'python3'}])
    # start sharding and block till it finishes
    traverse_chunks(pattern, workers, pid_python)
    # Stop Python process
    :python.stop(pid_python)
    # noreply
    {:noreply, pattern}
  end
  
  # Get smallest node (by length)
  defp get_smallest_worker(length) do
    Helpers.ProcessesGetter.get_workers(:fetch_config)
    |> Enum.map(fn
      x -> {:rpc.call(x, LocalSharder, :count_patterns_bylength,
	     [Supervisor, length]), x} end)
    |> Enum.min
    |> (fn {_, node_lname} -> node_lname end).()
  end

  # Traverse a list of strings by providing the number of steps, used
  # in sharding to avoid overload of OPT messages while sharding so
  # we chunk data and traverse them
  defp traverse_chunks(list_, workers, pid_python, offset \\ 20000) do
    IO.inspect(list_)
    IO.inspect(workers)
    IO.inspect(pid_python)
    IO.inspect(offset)
    if length(list_) <= offset do
      addresses = Task.async(fn -> :python.call(
      	pid_python, :patterns_handler,
      	:'PatternsHandler.chunk_patterns_byworkers', [list_, workers])
      end)
      Task.await(addresses)
      |> Enum.each(fn {x, y} ->
	:rpc.call(x, StringMatching.Sharder, :dispatch_patterns, [y])
      end)
    else
      addresses = Task.async(fn ->
	:python.call(
	  pid_python, :patterns_handler,
	  :'PatternsHandler.chunk_patterns_byworkers',
	  [Enum.take(list_, offset), workers]) end)
      Task.await(addresses)
      |> Enum.each(fn {x, y} ->
	:rpc.call(x, StringMatching.Sharder, :dispatch_patterns, [y])
      end)
      Enum.take(list_, offset-length(list_))
      |> traverse_chunks(workers, pid_python, offset)
    end
  end

  # Add pattern to a register
  def register_patterns(pattern, length) when is_binary(pattern) do
    Patterns.Registers.Map.get(length)
    |> Patterns.Register.add_patterns(pattern)
  end

  # Check if the pattern is the cluster
  def is_incluster(pattern, pattern_l) when is_binary(pattern) do
    # Get all registers of pattern_l length (from our mapping) and
    # their patterns
    {patterns, _} = Patterns.Registers.Map.get(pattern_l)
    |> Patterns.Register.get
    # Exists in the patters
    MapSet.member?(patterns, pattern)
  end
  # Get all already registered patterns from a list
  def filter_registered(patterns) do
    # Get all registers
    Patterns.Registers.Map.get
    |> Enum.reduce(MapSet.new(patterns), fn {x, y}, acc ->
      {reg_patterns, _} =  Patterns.Register.get(y)
      acc = MapSet.difference(acc, reg_patterns) end)
    |> MapSet.to_list
  end

  # Private: Register cluster sharders processes under
  # the supervisor pid
  defp via(name), do: Cluster.Sharders.Registry.via(name)
end
