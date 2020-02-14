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
  def new(length), do: %Needles{patterns: MapSet.new(), length: length} 
    
  @doc """
  Add new non blank pattern or patterns (length should be unique)
  """
  def add(needles, string) when is_blank(string), do: needles
  def add(needles, string) when is_binary(string) do
    string_length = String.length(string)
    if string_length != needles.length do
      IO.warn("Invalid string length #{string}")
      needles
    else
      %Needles{
	patterns: MapSet.put(needles.patterns, string),
	length: string_length
      }
    end
  end
  def add(needles, strings) do
    # filter strings that have different length
    patterns = strings
    |> Enum.filter(fn x -> String.length(x) == needles.length end)
    new_patterns = patterns |> MapSet.new
    %Needles{
      patterns: MapSet.union(new_patterns, needles.patterns),
      length: needles.length}
  end

  @doc """
  Remove Patterns from needles
  """
  def remove(needles, strings) do
    # filter strings that have different length
    patterns = strings
    |> MapSet.new
    new_patterns = MapSet.difference(needles.patterns, patterns)
    %Needles{patterns: new_patterns, length: needles.length}
  end

  
  @doc """
  match for a pattern in a string (recursive)
  TODO (optimize)
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
    ngrams = FastNgram.letter_ngrams(string, needles.length)
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
    |> Enum.with_index(0)
    |> Enum.reduce(%{}, fn {k, v}, acc -> Map.update(
      acc, k, [v], fn x -> Enum.concat([v], x) end) end)
  end
  
  # Get a substring from a string based on position and length
  defp slice(string, start_pos, length),
    do: String.slice(string, start_pos..start_pos+length-1)
       
end





      
