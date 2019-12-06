defmodule Client.Constructor do
  @moduledoc"""
  DSPS client node starter
  """
  use Application
  @name __MODULE__

  def start(_args, _opts) do
    children = [
      { Client.EndPoint, []}
    ]
    opts = [strategy: :one_for_one, name: @name]
    Supervisor.start_link(children, opts)
  end
end
