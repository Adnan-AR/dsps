defmodule RabinKarp.Test do
  use ExUnit.Case, async: true
  alias RabinKarp.Interface, as: RabinKarp
  doctest RabinKarp

  describe "create new needles group in a Rabon Karp system" do
    test "We should get the type Needles (empty)" do
      empty_needles = %Needles{
	lengths: MapSet.new, min_length: nil, patterns: Map.new}
      assert  empty_needles == RabinKarp.new
    end
  end

  describe "add blank to the patterns" do
    test "needles should stay empty" do
      needles = RabinKarp.new
      needles = RabinKarp.add(needles, "")
      empty_needles = %Needles{
	lengths: MapSet.new, min_length: nil, patterns: Map.new}
      assert empty_needles == needles
    end
  end

  describe "add a needle to an empty patterns" do
    test "we should find emoty element in the needles" do
      string = "test1"
      string_hash = Helpers.Hash.hash_string(string)
      needles = RabinKarp.new
      needles = RabinKarp.add(needles, string)
      expected_needles = %Needles{
	lengths: MapSet.new([5]),
	min_length: 5,
	patterns: %{string_hash => string}}
      assert expected_needles == needles
    end
  end

  describe "add a needle with smaller length to the patterns" do
    test "Needles min length should be modified" do
      string_1 = "test1"
      string_2 = "min1"
      string_hash_1 = Helpers.Hash.hash_string(string_1)
      string_hash_2 = Helpers.Hash.hash_string(string_2)
      needles = %Needles{
	lengths: MapSet.new([5]),
	min_length: 5,
	patterns: %{string_hash_1 => string_1}
      }
      needles = RabinKarp.add(needles, "min1")
      expected_needles = %Needles{
	lengths: MapSet.new([5,4]),
	min_length: 4,
	patterns: %{
	  string_hash_1 => string_1,
	  string_hash_2 => string_2
	}
      }
      assert expected_needles == needles
    end
  end

  describe "add a needle with bigger length to the patterns" do
    test "Needles min length should stay the same" do
      string_1 = "test1"
      string_2 = "bigtest1"
      string_hash_1 = Helpers.Hash.hash_string(string_1)
      string_hash_2 = Helpers.Hash.hash_string(string_2)
      needles = %Needles{
	lengths: MapSet.new([5]),
	min_length: 5,
	patterns: %{string_hash_1 => string_1}
      }
      needles = RabinKarp.add(needles, "bigtest1")
      expected_needles = %Needles{
	lengths: MapSet.new([5,8]),
	min_length: 5,
	patterns: %{
	  string_hash_1 => string_1,
	  string_hash_2 => string_2
	}
      }
      assert expected_needles == needles
    end
  end

  describe "Match any needle in the string" do
    test "Simple test, should be developed (edge cases)" do
      string = "I am adnan and building dsps system"
      needles = RabinKarp.add(RabinKarp.new, "adnan")
      expected_results= [{"adnan", 5, 9}]
      assert expected_results == RabinKarp.match(
	needles, string, 5, String.length(string), 0)
    end
  end

  describe "Match all needles in the string" do
    test "Simple test, should be developed (edge cases)" do
      string = "I am adnan and building dsps system and still adnan"
      needles = RabinKarp.add(RabinKarp.new, "adnan")
      |> RabinKarp.add("I am")
      |> RabinKarp.add("dsps system")
      |> RabinKarp.add("still_unkonwn")
      expected_results= MapSet.new(
	[
	  {"I am", 0, 3}, {"adnan", 5, 9},
	  {"adnan", 46, 50}, {"dsps system", 24, 34}
	]
      )
      assert expected_results == RabinKarp.search(needles, string)
    end
  end

end
