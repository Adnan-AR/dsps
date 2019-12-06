defmodule Helpers.Hash do
  @moduledoc """
  Module that load the hash function used across the cluster
  """
  @doc """
  Hash function unsing md5 by default
  """
  def hash_string(string, algorithm \\ :md5),
    do: :crypto.hash(algorithm, string) |> Base.encode16
end
