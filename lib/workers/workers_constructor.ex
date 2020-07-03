defmodule Workers.Constructor do
  @moduledoc"""
  DSPS workers constructor: start them in dynamic supervisor env
  """
  @name __MODULE__
  use Supervisor

  def start_link(_args) do
    children = [
      { StringMatching.Dsupervisor, []},
      { StringMatching.Sharder, []},
      { Node.Servers, Map.new},
      { Registry, [keys: :unique, name: StringMatching.Servers.Registry]},
      { Registry, [keys: :unique, name: StringMatching.Metadata.Registry]}
    ]
    opts = [strategy: :one_for_one, name: @name]
    Supervisor.start_link(children, opts)
  end
end
