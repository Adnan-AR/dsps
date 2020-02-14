defmodule Node.MetadataTest do
  use ExUnit.Case, async: true
  alias Node.Servers, as: Agent
  doctest Node.Servers

  describe "Init a metadata agent, add servers and get them" do
    test "Include three behaviors of Node.Metadata, start, add and get" do
      expected = %{
	1=>MapSet.new([:w1,:w2]),
        2=>MapSet.new([:w3,:w4]),
	3=>MapSet.new([:w5])}
      Agent.start_link(%{})
      Agent.add_server(:w1, 1)
      Agent.add_server(:w2, 1)
      Agent.add_server(:w3, 2)
      Agent.add_server(:w3, 2)
      Agent.add_server(:w4, 2)
      Agent.add_server(:w5, 3)
      assert expected == Agent.get
    end
  end

end
