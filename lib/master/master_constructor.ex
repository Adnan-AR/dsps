defmodule Master.Constructor do
  @moduledoc"""
  DSPS master node starter
  """
  use Application
  @name __MODULE__

  def start(_args, _opts) do
    children = [
      { Cluster.Orchestrer, []},
      { Cluster.Sharders.Dsupervisor, []},
      { Patterns.Registers.Map, Map.new},
      { Registry, [keys: :unique, name: Cluster.Sharders.Registry]},
      { Registry, [keys: :unique, name: Patterns.Register.Registry]}
      
    ]
    opts = [strategy: :one_for_one, name: @name]
    Supervisor.start_link(children, opts)
  end
end
