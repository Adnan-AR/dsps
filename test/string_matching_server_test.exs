defmodule StringMatching.ServerTest do
  use ExUnit.Case, async: true
  alias StringMatching.Interface, as: Worker
  alias StringMatching.Dsupervisor, as: Dsupervisor
  doctest StringMatching.Server

  describe "update/2" do
    test "update Aha-Corasick automaton with new patterns" do
      name = :name
      patterns = ["test1", "test2", "test3"]
      Worker.start_link(name)
      res = Worker.update(name, patterns)
      assert :ok == res
    end
  end

  describe "search/2" do
    test "search for srting patterns in a string (Todo: edge cases)" do
      name = :name
      string = "I am test1, then I test test2, to finish test3"
      patterns = ["test1", "test2", "test3"]
      # start a string matching worker/server via DynamicSupervisor
      # because we need the metadata agent also
      Dsupervisor.start_string_matching(name)
      Worker.update(name, patterns)
      results = Worker.search(name, string)
      expected = [{"test1", 6, 5}, {"test2", 25, 5}, {"test3", 42, 5}]
      assert expected == results
    end
  end
end
