defmodule Cluster.Orchestrer do
  @moduledoc"""
  Sharder of StringMatching processes, the Sharder contact 
  StringMatching Servers that exist in the Regsitry via 
  GenServer
  """
  use GenServer
  require Logger
  @name __MODULE__
  @nodes Application.fetch_env!(:dsps, :nodes)
  
  @doc """
  Start the orcherstrer
  """
  def start_link(_arg),
    do: GenServer.start_link(__MODULE__, :ok, name: @name)

  @doc """
  Init the Orcherstrer
  """
  def init(:ok),
    do: {:ok, %{}}

  @doc """
  API: connect a list of nodes using Long Name
  """
  def connect_nodes(node_lnames),
    do: GenServer.cast(@name, {:connect_nodes, node_lnames})
  
  @doc """
  API: connect a list of nodes using Long Name
  """
  def connect_nodes,
    do: GenServer.cast(@name, {:connect_nodes})

  @doc """
  API: disconnect a list of nodes using Long Name
  """
  def disconnect_nodes(node_lnames),
    do: GenServer.cast(@name, {:disconnect_nodes, node_lnames})

  @doc """
  API (recursive): Create a number of String Matching servers 
  on a specific node
  """
  def create_sm_servers(node_lname, how_many)  when how_many <= 1 do
    GenServer.cast(@name, {:create_sm_server, node_lname})
  end
  def create_sm_servers(node_lname, how_many)  do
    GenServer.cast(@name, {:create_sm_server, node_lname})
    create_sm_servers(node_lname, how_many - 1) 
  end
  
  @doc """
  API: Get workers list
  """
  def get_workers,
    do: GenServer.call(@name, {:get_worker_nodes})
    
  @doc """
  Callback to connect to a list of nodes
  """
  def handle_cast({:connect_nodes, node_lnames}, _state) do
    Enum.each(node_lnames, fn x -> x
    |> String.to_atom
    |> Node.connect
    end)
    Logger.info("Connecting to #{node_lnames}")
    {:noreply, node_lnames}
  end

  @doc """
  Callback to connect to a list of nodes
  """
  def handle_cast({:connect_nodes}, _state) do
    nodes = Map.values(@nodes)
    |> Enum.flat_map(fn x -> x end)
    nodes
    |> Enum.map(fn x -> x
    |> String.to_atom
    |> Node.connect
    end)
    Logger.info("Connecting to #{nodes}")
    {:noreply, nodes}
  end

  @doc """
  Callback to disconnect from a list of nodes
  """
  def handle_cast({:disconnect_nodes, node_lnames}, _state) do
    Enum.each(node_lnames, fn x -> x
    |> String.to_atom
    |> Node.disconnect
    end)
    Logger.info("Disconnecting from #{node_lnames}")
    {:noreply, node_lnames}
  end

  @doc """
  Callback: Create a number of String Matching
  servers on a specific node
  """
  def handle_cast({:create_sm_server, node_lname}, _state) do
    id = UUID.uuid4() 
    node_lname
    |> String.to_atom
    |> :rpc.call(StringMatching.Dsupervisor, :start_string_matching,[id])
    Logger.info("Creating String Matching server on #{node_lname}")
    {:noreply, node_lname}
  end

  @doc """
  Callback to handle search using all automatons
  """
  def handle_call({:get_worker_nodes}, _from, state),
    do: {:reply, Node.list, state}
end
