defmodule Needles do
  @docmodule """
  Patterns data structure definition
  """

  defstruct [
    patterns: Map.new(),
    lengths: MapSet.new(),
    min_length: nil
  ]

  @typedoc """
  This is the structure to hold patterns

  * `:patterns`: contains the patterns of string matching system
  * `:lengths`: contains the different lengths of patterns
  """
  @type t :: %__MODULE__{
    patterns: Map.t,
    lengths: MapSet.t,
    min_length: nil | pos_integer
  }
end
