use serde_json::Value;
fn main() {
    let v: Value = serde_json::from_str("{\"msg\":\"crates works\"}").unwrap();
    println!("{}", v["msg"]);
}
