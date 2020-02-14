defmodule Patterns.RegisterTest do
  use ExUnit.Case, async: false
  alias Patterns.Register, as: PR
  doctest Patterns.Register
  
  describe "get/1" do
    test "get all the data in a Patterns Register" do
      # Init the constructor just for the Registery (not the register)
      :timer.sleep(500)
      Master.Constructor.start(:whatever, :whatever)
      # test
      name = :p1
      length = 5 
      expected = {
	MapSet.new(["test1", "test2", "test3", "test4"]), length
      }
      patterns = ["test1", "test2", "test3", "test14", "test4"]
      PR.start_link(name, length)
      PR.add_patterns(name, patterns)
      assert expected == PR.get(name)
      
    end
  end

  describe "add_patterns/2" do
    test "add data to an register with some repetitions"do
      # Init the constructor just for the Registery (not the register)
      :timer.sleep(1000)
      Master.Constructor.start(:whatever, :whatever)
      name = :p2
      length = 5
      expected = {
	MapSet.new(["test1", "test2", "test3", "test4"]), length
      }
      patterns = ["test1", "test2", "test3", "#18298",
		  "test14", "test4", "test4", ""]
      PR.start_link(name, length)
      PR.add_patterns(name, patterns)
      assert expected == PR.get(name)
      
    end
  end

  
  describe "add_patterns/2 one word" do
    test "add one pattern to a non empty agent with some repetitions"do
      # Init the constructor just for the Registery (not the register)
      :timer.sleep(1500)
      Master.Constructor.start(:whatever, :whatever)
      name = :p3
      length = 5
      expected = {MapSet.new(["test1"]), length}
      patterns = "test1"
      PR.start_link(name, length)
      PR.add_patterns(name, patterns)
      assert expected == PR.get(name)
      
    end
  end

end
