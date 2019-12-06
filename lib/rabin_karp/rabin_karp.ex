defmodule RabinKarp do
  @moduledoc """
  Usage:

  ```elixir
  dictionary = RabinKarp.new(["my", "dictionary", "terms"])
  results = RabinKarp.search(dictionary, 
    "I wonder if any of the terms from my dictionary appear
     in this text, and if so, where?")

  => #MapSet<[{"dictionary", 37, 10}, {"my", 34, 2}, {"terms", 23, 5}]>
  ```
  """
  @behaviour RabinKarp.Interface.Behaviour

  # To check if a string in blank
  defguardp is_blank(string) when byte_size(string) == 0

  @doc """
  Construct a Needles group
  """
  def new, do: %Needles{}
    
  @doc """
  Add new non blank pattern
  """
  def add(needles, string) when is_blank(string), do: needles
  def add(needles, string) do
    string_length = String.length(string)
    string_hash = Helpers.Hash.hash_string(string)
    %Needles{
      patterns: Map.put(needles.patterns, string_hash, string),
      lengths: MapSet.put(needles.lengths, string_length),
      min_length: min(needles.min_length, string_length)
    }
  end

  @doc """
  match for a pattern in a string (recursive)
  """
  def match(needles, string, pattern_length, string_length, position)
    when string_length - position < pattern_length, do: []
  def match(needles, string, pattern_length, string_length, position) do
      string_slice = slice(string, position, pattern_length)
      hash_slice = Helpers.Hash.hash_string(string_slice)
      if  Map.has_key?(needles.patterns, hash_slice) and
          Map.fetch!(needles.patterns, hash_slice) == string_slice  do
	Enum.concat(
	  [{string_slice, position, position+pattern_length-1}],
	  match(needles, string, pattern_length, string_length, position+1))
      else
	Enum.concat(
	  [],
	  match(needles, string, pattern_length, string_length, position+1))
      end
   end

  @doc """
  search for needles in a string
  """ 
  def search(needles, string) do
    lengths = MapSet.to_list(needles.lengths) 
    string_length = String.length(string)
    Helpers.Parallel.pmap(lengths, fn x ->
      __MODULE__.match(needles, string, x, string_length, 0) end)
    |> Enum.flat_map(fn x -> x end)
    |> MapSet.new    
  end
      
  # Get a substring from a string based on position and length
  defp slice(string, start_pos, length),
    do: String.slice(string, start_pos..start_pos+length-1)
       
end
