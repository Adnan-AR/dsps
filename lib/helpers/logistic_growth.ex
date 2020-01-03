defmodule Helpers.LogisticGrowth do
  @moduledoc"""
  Logistic growth module that should be used to get the number of
  shards by number of words
  """

  @doc """
  Compute the number of servers by the number of words (cf.
  logistic growth function)
  """
  def compute_number(nb_words, r \\ 1.0e-5, k \\ 10) do
    List.duplicate(1, nb_words)
    |> Enum.reduce(fn n, acc ->  acc + r*acc*(1-acc/k) end)
    |> round 
  end
end

    
