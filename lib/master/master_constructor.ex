defmodule Master.Constructor do
  @moduledoc"""
  DSPS master node starter
  """
  @name __MODULE__

  use Supervisor
  def start_link(_args) do
    children = [
      { Cluster.Orchestrer, []},
      { Cluster.Sharders.Dsupervisor, []},
      { Patterns.Registers.Map, Map.new},
      { Registry, [keys: :unique, name: Cluster.Sharders.Registry]},
      { Registry, [keys: :unique, name: Patterns.Register.Registry]}
      
    ]
    opts = [strategy: :one_for_one, name: @name]
    # Save the results
    res = Supervisor.start_link(children, opts)
    # Connect to workers
    Cluster.Orchestrer.connect_nodes
    # Start a sharder
    Cluster.Sharders.Dsupervisor.start_cluster_sharder("1")
    # Sleep one second
    :timer.sleep(1000)
    # Init Rabin-Karp workers on all nodes
    2..125 |> Enum.reduce(Map.new, fn x, acc ->Map.put(acc, x, 1000) end) |> Cluster.Orchestrer.init_workers
    # callback the results
    res
  end
end
