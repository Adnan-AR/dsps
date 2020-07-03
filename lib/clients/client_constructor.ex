defmodule Client.Constructor do
  @moduledoc"""
  DSPS client node starter
  """
  use Supervisor
  @name __MODULE__

  def start_link(_args) do
    children = [
      { Client.EndPoint, []}
    ]
    opts = [strategy: :one_for_one, name: @name]
    Supervisor.start_link(children, opts)
  end
end
