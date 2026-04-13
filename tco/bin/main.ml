open Core
open Core_bench

let rec factorial n =
  match n with
  | 0 | 1 -> 1
  | n -> n * factorial (n - 1)

let factorial_tco n =
  let rec helper cur acc =
    match cur with
    | 0 | 1 -> acc
    | cur -> (helper [@tailcall]) (cur - 1) (acc * cur)
  in
  helper n 1

let cnt = 1000

(* Benchmark *)
let bench () =
  Bench.make_command
    [
      Bench.Test.create ~name:"factorial" (fun () -> factorial cnt);
      Bench.Test.create ~name:"factorial_tco" (fun () -> factorial_tco cnt);
    ]
  |> Command_unix.run

let _ = bench ()
