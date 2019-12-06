defmodule Client.EndPoint do
  @moduledoc"""
  The Client end point is the module that performs pattern matching 
  queries to cluster, the response is returned on this module. There
  is one end point per node
  """
  use GenServer
  @name __MODULE__

  @doc """
  Start the end point
  """
  def start_link(_arg),
    do: GenServer.start_link(__MODULE__, :ok, name: @name)

  @doc """
  Init the client
  """
  def init(:ok),
    do: {:ok, %{}}

  @doc """
  API: perform pattern matching query
  Infinity timeout is set
  """
  def match(string),
    do: GenServer.call(@name, {:match_query, string}, :infinity)

  @doc """
  API: perform pattern matching queries in bulk
  Infinity timeout is set
  """
  def bulk_match(strings) do
    call = fn x ->
      GenServer.call(@name, {:match_query, x}, :infinity) end
    Helpers.Parallel.pmap(strings, call)
  end  

  @doc """
  callback to send the queries across the cluster nodes
  """
  def handle_call({:match_query, string}, _from, state) do
    # TODO: get only worker nodes
    results = Helpers.ProcessesGetter.get_workers(:fetch_config)
    |> :rpc.multicall(StringMatching.Sharder, :fully_search, [string])
    # Flatting results from worker nodes
    |> (fn {x, _} -> x end).()
    |> Enum.flat_map(fn x -> x end)
    # Reply
    {:reply, results, state}
  end
end
