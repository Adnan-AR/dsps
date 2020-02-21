defmodule Node.Starter do
  @moduledoc """
  Node Initializer
  """

  use Application
  
  # Rename node
  defp rename_node do
    # Fetch name
    lname = Application.fetch_env!(:dsps, :node_name)
    |> String.to_atom
    # Stop the node
    :net_kernel.stop()
    # rename the node
    :net_kernel.start([lname, :longnames])
  end

  # Set Cluster cookie (name)
  defp set_cookie do
    # Fetch the magic cookie (cluster name)
    Application.fetch_env!(:dsps, :node_name)
    |> String.to_atom
    |> Node.set_cookie
  end

  # Start node
  def start(_type, _args) do
    rename_node
    set_cookie
    node_t =  Application.fetch_env!(:dsps, :node_type)
    # If it is a master
    if Map.get(node_t, "master") do
      # Init master
      Master.Constructor.start(:ok,:ok)
      # Connect to workers
      Cluster.Orchestrer.connect_nodes
      # Start a sharder
      Cluster.Sharders.Dsupervisor.start_cluster_sharder("1")
      # Init Rabin-Karp workers on all nodes
      2..125
      |> Enum.reduce(Map.new, fn x, acc ->Map.put(acc, x, 1000) end)
      |> Cluster.Orchestrer.init_workers
    end
    # If it is a worker
    if Map.get(node_t, "worker"), do: Workers.Constructor.start(:ok,:ok)
    # If it is a client
    if Map.get(node_t, "worker"), do: Client.Constructor.start(:ok,:ok)
  end
end



    
  
