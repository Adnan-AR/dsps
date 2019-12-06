defmodule Workers.Constructor do
  @moduledoc"""
  DSPS workers constructor: start them in dynamic supervisor env
  """
  use Application
  @name __MODULE__

  def start(_args, _opts) do
    children = [
      { StringMatching.Dsupervisor, []},
      { StringMatching.Sharder, []},
      { Node.Metadata, {0, 0, []}},
      { Registry, [keys: :unique, name: StringMatching.Servers.Registry]},
      { Registry, [keys: :unique, name: StringMatching.Metadata.Registry]}
    ]
    opts = [strategy: :one_for_one, name: @name]
    Supervisor.start_link(children, opts)
  end
end
