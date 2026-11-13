//! Small FFI string helpers shared by the kits' Win32 layers.
//!
//! `to_wide` / `from_wide` are the pair a dozen kits each
//! re-implemented privately in their platform modules
//! (PAIN_POINTS #53). New platform code should call these; the
//! existing private copies are being retired kit by kit.

/// Encode a string as a NUL-terminated UTF-16 buffer, the shape
/// most Win32 `*W` APIs expect.
pub fn to_wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

/// Decode a UTF-16 buffer up to (not including) its first NUL,
/// lossy on unpaired surrogates — the right behavior for strings
/// Windows hands back (paths, names, descriptions).
pub fn from_wide(buf: &[u16]) -> String {
    let end = buf.iter().position(|&c| c == 0).unwrap_or(buf.len());
    String::from_utf16_lossy(&buf[..end])
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wide_roundtrip() {
        assert_eq!(to_wide("ab"), vec![b'a' as u16, b'b' as u16, 0]);
        assert_eq!(from_wide(&to_wide("C:\\Temp\\🎉")), "C:\\Temp\\🎉");
        assert_eq!(from_wide(&[b'x' as u16, 0, b'y' as u16]), "x");
        assert_eq!(from_wide(&[]), "");
    }
}
