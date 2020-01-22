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
  def create_sm_servers(node_lname, length, how_many)  when how_many <= 1 do
    GenServer.cast(@name, {:create_sm_server,  node_lname, length})
  end
  def create_sm_servers(node_lname, length, how_many)  do
    GenServer.cast(@name, {:create_sm_server, node_lname, length})
    create_sm_servers(node_lname, length, how_many - 1) 
  end
    
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
  def handle_cast({:create_sm_server, node_lname, length}, _state) do
    id = UUID.uuid4() 
    node_lname
    |> :rpc.call(
      StringMatching.Dsupervisor, :start_string_matching, [id, length])
    Logger.info("Creating String Matching server on #{node_lname}")
    {:noreply, node_lname}
  end

  # This is to create a conveninent number of string matching servers
  # depending on volume of words
  def init_workers(nb_words_char) do
    workers = Helpers.ProcessesGetter.get_workers(:fetch_config)
    nb_words_char
    |> Enum.reduce(%{}, fn {x, y}, acc -> Map.put(
      acc, x, Helpers.LogisticGrowth.compute_number(y)) end)
    |> Enum.each(fn {x, y} -> distribute_workers(workers, x, y) end)
  end

  # Distribute string matchin servers on worker nodes evenly
  # E.g 4 workers and 10 string matching servers
  # W W W W
  # S S S S
  # S S S S
  # S S
  def distribute_workers(workers, length, how_many) when how_many > 0 do
    workers_num = length(workers)
    init_workers_num = div(how_many, workers_num)
    create = fn x ->
      create_sm_servers(x, length, init_workers_num) end
    add = fn x ->
      create_sm_servers(x, length, 1) end 
    if init_workers_num > 0, do: workers |> Enum.each(create)
    workers
    |> Enum.take(rem(how_many, workers_num))
    |> Enum.each(add)
  end  
end
