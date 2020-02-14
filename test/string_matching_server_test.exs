defmodule StringMatching.ServerTest do
  use ExUnit.Case, async: true
  alias StringMatching.Server.Interface, as: Worker
  alias StringMatching.Dsupervisor, as: Dsupervisor
  doctest RabinKarp.Server

  describe "update/2" do
    test "update Aha-Corasick automaton with new patterns" do
      name = :name
      length = 5
      patterns = ["test1", "test2", "test3", "test14"]
      Worker.start_link(name, length)
      res = Worker.update(name, patterns)
      assert :ok == res
    end
  end

  describe "search/2" do
    test "search for srting patterns in a string (Todo: edge cases)" do
      name = :name
      length = 5
      string = "I am test1, then I test test2, to finish test3"
      patterns = ["test1", "test2", "test3"]
      # start a string matching worker/server via DynamicSupervisor
      # because we need the metadata agent also
      Dsupervisor.start_string_matching(name, length)
      Worker.update(name, patterns)
      results = Worker.search(name, string)
      expected = [{"test1", [5]}, {"test2", [24]}, {"test3", [41]}]
      # kill the supervisor because it stays running in Erlang VM
      DynamicSupervisor.stop(Dsupervisor)
      # Assert
      assert expected == results      
    end
  end 
end
