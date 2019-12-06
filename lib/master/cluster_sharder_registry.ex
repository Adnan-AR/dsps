defmodule Cluster.Sharders.Registry do
  @moduledoc"""
  Registry to store cluster sharders identity
  """
  @module __MODULE__
  def via(name), do: {:via, Registry, {@module,name}}
end
