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
  def add(needles, string) when is_binary(string) do
    string_length = String.length(string)
    # string_hash = Helpers.Hash.hash_string(string)
    %Needles{
      patterns: MapSet.put(needles.patterns, string),
      lengths: MapSet.put(needles.lengths, string_length),
      min_length: min(needles.min_length, string_length)
    }
  end
  def add(needles, strings) do
    string_lengths = strings
    |> Enum.map(fn x -> String.length(x) end)
    min_length = string_lengths |> Enum.min
    new_patterns = strings
    |> Enum.reduce(
      MapSet.new, fn x, acc -> MapSet.put(acc, x) end)
    new_lengths = strings
    |> Enum.reduce(
      MapSet.new, fn x, acc -> MapSet.put(acc, String.length(x)) end)
    %Needles{
      patterns: new_patterns,
      lengths: new_lengths,
      min_length: min(needles.min_length, min_length)
    }
  end
  @doc """
  match for a pattern in a string (recursive)
  """
  def match(_needles, _string, pattern_length, string_length, position)
    when string_length - position < pattern_length, do: []
  def match(needles, string, pattern_length, string_length, position) do
      string_slice = slice(string, position, pattern_length)
      if  MapSet.member?(needles.patterns, string_slice) do
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
    ngrams = FastNgram.letter_ngrams(string, needles.min_length)
    ngrams_pos = ngrams |> indexify
    ngrams
    |> MapSet.new
    |> MapSet.intersection(needles.patterns)
    |> Enum.map(fn x -> {x, Map.get(ngrams_pos, x)} end)
    |> MapSet.new
  end

  # map the positions of all n-grams
  def indexify(enumerable) do
    enumerable
    |> Enum.with_index(1)
    |> Enum.reduce(%{}, fn {k, v}, acc -> Map.update(
      acc, k, [v], fn x -> Enum.concat([v], x) end) end)
  end
  
  # Get a substring from a string based on position and length
  defp slice(string, start_pos, length),
    do: String.slice(string, start_pos..start_pos+length-1)
       
end





      
