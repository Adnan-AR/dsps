defmodule Helpers.Parallel do
  @moduledoc"""
  Implemtation of parallel stuff
  """

  @doc """
  Synchronous parallel mapping function
  Set timeout to :infinity if needed
  """
  def pmap(collection, func, timeout \\ 5000) do
    collection
    |> Enum.map(&(Task.async(fn -> func.(&1) end)))
    |> Enum.map(fn x -> Task.await(x, timeout) end)
  end

  @doc """
  Asynchronous parallel mapping function
  """
  def pmap_async(collection, func),
    do: collection |> Enum.map(&(Task.async(fn -> func.(&1) end)))
  
end
