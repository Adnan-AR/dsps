defmodule Patterns.Register.Registry do
  @moduledoc"""
  Registry to store Patterns readers servers identity
  """
  @module __MODULE__
  def via(name), do: {:via, Registry, {@module,name}}
end
