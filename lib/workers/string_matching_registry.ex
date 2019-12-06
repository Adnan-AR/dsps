defmodule StringMatching.Servers.Registry do
  @moduledoc"""
  Registry to store StringMatching servers identity
  """
  @module __MODULE__
  def via(name), do: {:via, Registry, {@module,name}}
end
