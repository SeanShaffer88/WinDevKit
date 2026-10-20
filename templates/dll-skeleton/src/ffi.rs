//! C ABI surface — everything declared in include/{{HEADER}}.
//! Conventions (house standard, from WinRecovery):
//! - `*mut c_char` results are caller-owned; free with `{{PREFIX}}_free_string`.
//! - Failures return null / an ERR_* code + a thread-local last-error message.
//! - Nothing unwinds across the FFI boundary (catch_unwind everywhere;
//!   release profile also sets panic = "abort").

use std::cell::RefCell;
use std::ffi::CString;
use std::os::raw::{c_char, c_int};

thread_local! {
    static LAST_ERROR: RefCell<(i32, CString)> =
        RefCell::new((0, CString::new("").unwrap()));
}

pub fn set_error(code: i32, msg: &str) {
    LAST_ERROR.with(|e| {
        *e.borrow_mut() = (
            code,
            CString::new(msg).unwrap_or_else(|_| CString::new("error").unwrap()),
        );
    });
}

#[no_mangle]
pub extern "C" fn {{PREFIX}}_version() -> *const c_char {
    static VERSION_C: &[u8] = b"0.1.0\0";
    VERSION_C.as_ptr() as *const c_char
}

#[no_mangle]
pub extern "C" fn {{PREFIX}}_last_error() -> *const c_char {
    LAST_ERROR.with(|e| e.borrow().1.as_ptr())
}

#[no_mangle]
pub extern "C" fn {{PREFIX}}_last_error_code() -> c_int {
    LAST_ERROR.with(|e| e.borrow().0) as c_int
}

/// # Safety (caller contract): `p` is null or a string this library
/// returned and has not been freed yet. Documented in the header.
#[allow(clippy::not_unsafe_ptr_arg_deref)]
#[no_mangle]
pub extern "C" fn {{PREFIX}}_free_string(p: *mut c_char) {
    if !p.is_null() {
        unsafe {
            drop(CString::from_raw(p));
        }
    }
}
