defmodule Needles do
  defstruct [
    patterns: MapSet.new(),
    lengths: MapSet.new(),
    min_length: nil
  ]

  @typedoc """
  This is the structure to hold patterns

  * `:patterns`: contains the patterns of string matching system
  * `:lengths`: contains the different lengths of patterns
  * `:min_length`: minimum length in the needles
  """
  @type t :: %__MODULE__{
    patterns: MapSet.t,
    lengths: MapSet.t,
    min_length: nil | pos_integer
  }
end
