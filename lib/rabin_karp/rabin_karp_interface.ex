defmodule RabinKarp.Interface do
  @moduledoc """
  Rabin-Karp interface.
  """
  
  defmodule Behaviour do
    @callback new :: Needles.t
    @callback add(Needles.t, String.t) :: Needles.t
    @callback add(Needles.t, list(String.t), Integer.t) :: Needles.t
    @callback match(Needles.t, String.t, Integer.t,
      Integer.t, Integer.t) :: List.t
    @callback search(Needles.t, String.t) :: MapSet.t
  end

  @spec new :: Needles.t
  def new, do: RabinKarp.new
  
  @spec add(Needles.t, String.t) :: Needles.t
  def add(needles, string), do: RabinKarp.add(needles, string)

  @spec add(Needles.t, list(String.t), Integer.t) :: Needles.t
  def add(needles, strings, length), do: RabinKarp.add(
	needles, strings, length)
  
  @spec match(Needles.t, String.t, Integer.t,
    Integer.t, Integer.t) :: List.t
  def match(needles, string, pattern_length, string_length, position),
    do: RabinKarp.match(
	  needles, string, pattern_length, string_length, position)
  
  @spec search(Needles.t, String.t) :: MapSet.t
  def search(needles, string), do: RabinKarp.search(needles, string)
  
end
