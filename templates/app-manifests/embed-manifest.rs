// build.rs snippet — embed app.manifest into a Rust binary without extra
// crates, using the Windows SDK resource compiler via a tiny .rc file.
// For most projects `winresource` or `embed-resource` is the easier route;
// this dependency-free variant uses rc.exe from the SDK (present on
// windows-latest CI and any VS Build Tools install).
//
// fn main() {
//     if std::env::var("CARGO_CFG_TARGET_OS").as_deref() == Ok("windows") {
//         println!("cargo:rerun-if-changed=app.manifest");
//         println!("cargo:rerun-if-changed=app.rc");
//         let out = std::env::var("OUT_DIR").unwrap();
//         let obj = format!("{out}\\app.res");
//         let status = std::process::Command::new("rc.exe")
//             .args(["/nologo", "/fo", &obj, "app.rc"])
//             .status()
//             .expect("rc.exe (Windows SDK) is required to embed the manifest");
//         assert!(status.success(), "rc.exe failed");
//         println!("cargo:rustc-link-arg={obj}");
//     }
// }
//
// And app.rc next to build.rs contains exactly one line:
//   1 RT_MANIFEST "app.manifest"
// (RT_MANIFEST's numeric id is 24; if rc.exe rejects the name, use:
//   1 24 "app.manifest")
