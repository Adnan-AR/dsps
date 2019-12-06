defmodule Cluster.Sharder do
  @moduledoc"""
  Sharder of StringMatching processes, the Sharder contact 
  StringMatching Servers that exist in the Regsitry via 
  GenServer
  """
  use GenServer
  require Logger
  alias Node.Metadata, as: MetaAgent
  
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
  def dispatch_patterns([patterns_h | tail], name) when tail==[] ,
    do: GenServer.cast(via(name), {:global_dispatch, patterns_h})
  def dispatch_patterns([patterns_h | tail], name) do
    GenServer.cast(via(name), {:global_dispatch, patterns_h})
    dispatch_patterns(tail, name)
  end
  
  @doc """
  Callback to feed all nodes across cluster with pattern or add a
  single pattern
  """
  def handle_cast({:global_dispatch, pattern}, _state)
      when is_binary(pattern) do
    if is_incluster(pattern) do
      try do
	raise AlreadyExistError, pattern
      rescue
	e in AlreadyExistError -> IO.inspect(e)
      end
    else
      get_smallest_worker(:by_patterns_number)
      |> :rpc.call(
	StringMatching.Sharder, :dispatch_patterns, [pattern])
    end
    {:noreply, pattern}
  end


  # Get smallest node (by number of patterns or servers)
  defp get_smallest_worker(spec) do
    Helpers.ProcessesGetter.get_workers(:fetch_config)
    |> Enum.map(fn
      x when spec == :by_servers_number ->
	{:rpc.call(x, MetaAgent, :get,[:how_many_servers]), x}
      x -> {:rpc.call(x, MetaAgent, :get,[:how_many_patterns]), x}
    end)
    |> Enum.min
    |> (fn {_, node_lname} -> node_lname end).()
  end

  # Check if the pattern is the cluster
  defp is_incluster(pattern) do
    Helpers.ProcessesGetter.get_workers(:fetch_config)
    |> Enum.map(fn x
      -> :rpc.call(x, StringMatching.Sharder, :is_there, [pattern]) end)
    |> Enum.any?
  end

  # Private: Register cluster sharders processes under
  # the supervisor pid
  defp via(name), do: Cluster.Sharders.Registry.via(name)
end
