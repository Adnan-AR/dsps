defmodule RabinKarp.Test do
  use ExUnit.Case, async: true
  alias RabinKarp.Interface, as: RabinKarp
  doctest RabinKarp

  describe "create new needles group in a Rabon Karp system" do
    test "We should get the type Needles (empty)" do
      length=10
      empty_needles = %Needles{
	length: length, patterns: MapSet.new}
      assert  empty_needles == RabinKarp.new(length)
    end
  end

  describe "add blank to the patterns" do
    test "needles should stay empty" do
      length=10
      needles = RabinKarp.new(length)
      needles = RabinKarp.add(needles, "")
      empty_needles = %Needles{
	length: length, patterns: MapSet.new}
      assert empty_needles == needles
    end
  end

  describe "add a needle to an empty patterns" do
    test "we should find emoty element in the needles" do
      string = "test1"
      needles = String.length(string) |> RabinKarp.new
      needles = RabinKarp.add(needles, string)
      expected_needles = %Needles{
	length: String.length(string),
	patterns: MapSet.new([string])}
      assert expected_needles == needles
    end
  end

  describe "add a needle to a needles group with bad length" do
    test "we should find emoty element in the needles" do
      string = "test1"
      length = 10
      needles = length |> RabinKarp.new
      needles = RabinKarp.add(needles, string)
      expected_needles = %Needles{
	length: length,
	patterns: MapSet.new}
      assert expected_needles == needles
    end
  end

  describe "add a list of patterns to needles" do
    test "simple test" do
      s1 = "test1"
      s2 = "test2"
      s3 = "test3"
      s4 = "test13"
      s5 = "test4"
      s6 = "test5"
      l = 5
      expected_needles = %Needles{
	length: 5, patterns: MapSet.new([s1, s2, s3, s5, s6])}
      needles = RabinKarp.new(l) |> RabinKarp.add([s1, s2, s3, s4])
      needles = RabinKarp.add(needles, [s4, s5])
      needles = RabinKarp.add(needles, s6)
      needles = RabinKarp.add(needles, s4)
      assert expected_needles == needles
    end
  end

  describe "Match any needle in the string" do
    test "Simple test, should be developed (edge cases)" do
      string = "I am adnan and building dsps system"
      l = 5
      needles = RabinKarp.new(l) |> RabinKarp.add("adnan")
      expected_results= [{"adnan", 5, 9}]
      assert expected_results == RabinKarp.match(
	needles, string, 5, String.length(string), 0)
    end
  end

  describe "Match all needles in the string" do
    test "Simple test, should be developed (edge cases)" do
      string = "I am adnan and building dsps system and still adnan"
      l = 5 
      needles = RabinKarp.new(l) |> RabinKarp.add("adnan")
      |> RabinKarp.add(["I am ", "dsps system", "still_unkonwn"])
      expected_results = MapSet.new(
	[{"I am ", [0]}, {"adnan", [46, 5]}])
      assert expected_results == RabinKarp.search(needles, string)
    end
  end

  describe "Remove patterns from needles" do
    test "Simple test, should be developed (edge cases)" do
      remove_list = ["test5", "test6", "test7"]
      l = 5 
      needles = RabinKarp.new(l) |> RabinKarp.add("test1")
      |> RabinKarp.add(["test2", "test3", "test4", "test5", "test6"])
      |> RabinKarp.remove(remove_list)
      expected_results = %Needles{
	length: 5, patterns: MapSet.new(
	  ["test1", "test2", "test3", "test4"])}
      assert expected_results == needles
    end
  end

end
