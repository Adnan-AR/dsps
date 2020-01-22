defmodule Needles do
  defstruct [
    patterns: MapSet.new(),
    length: nil
  ]

  @typedoc """
  This is the structure to hold patterns, each entity should hold
  unique length of patterns

  * `:patterns`: contains the patterns of string matching system
  * `:length`: length of the needles
  """
  @type t :: %__MODULE__{
    patterns: MapSet.t,
    length: nil | pos_integer
  }
end
