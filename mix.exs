defmodule Dsps.MixProject do
  use Mix.Project

  def project do
    [
      app: :dsps,
      version: "0.1.0",
      elixir: "~> 1.9",
      elixirc_paths: elixirc_paths(Mix.env),
      build_embedded: Mix.env == :prod,
      start_permanent: Mix.env == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      mod: {Workers.Constructor, []},
      extra_applications: [:logger]
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:aho_corasick, "~> 0.0.1"},
      {:csv, "~> 2.3"},
      {:uuid, "~> 1.1"},
      {:fast_ngram, "~> 1.0"}
    ]
  end
  # Add dependecies paths depending on build env
  defp elixirc_paths(:test), do: ["lib","test/fake"]
  defp elixirc_paths(_), do: ["lib"]

end
