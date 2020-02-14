defmodule StringMatching.MetadataTest do
  use ExUnit.Case, async: false
  alias StringMatching.Metadata, as: Agent
  doctest StringMatching.Metadata

  describe "get/1" do
    test "get all the metadata of a string matching server" do
      name = :name
      length = 5 
      expected = {MapSet.new(["test1", "test2", "test3", "test4"]),
		  4, "test4", length}
      patterns = ["test1", "test2", "test3", "test14", "test4"]
      Agent.start_link(name, {MapSet.new(patterns), length})
      assert expected == Agent.get(name) 
    end
  end

  describe "add_patterns/2" do
    test "add data to an empty agent with some repetitions"do
      name = :name
      length = 5
      expected = {MapSet.new(["test1", "test2", "test3", "test4"]),
		  4, "test4", length}
      patterns = ["test1", "test2", "test3", "#18298",
		  "test14", "test4", "test4", ""]
      Agent.start_link(name, {MapSet.new([]), length})
      Agent.add_patterns(name, patterns)
      assert expected == Agent.get(name) 
    end
  end

  
  describe "add_patterns/2 one word" do
    test "add one pattern to a non empty agent with some repetitions"do
      name = :name
      length = 5
      expected = {MapSet.new(["test1", "test2", "test3", "test4"]),
		  4, "test1", length}
      patterns = "test1"
      Agent.start_link(
	name, {MapSet.new(["test2", "test3", "test4"]), length})
      Agent.add_patterns(name, patterns)
      assert expected == Agent.get(name) 
    end
  end

end
