import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class MedRagTheme {
  // Eye-Catching Vibrant Dark Palette
  static const Color backgroundDark = Color(0xFF0B0C10); // Deep Space
  static const Color surfaceDark = Color(0xFF1F2833); // Elevation 1
  static const Color primaryCyan = Color(0xFF45F3FF); // Bright Neon Cyan
  static const Color secondaryCoral = Color(0xFFFF2A7A); // Electric Coral
  static const Color textLight = Color(0xFFE0E6ED);
  static const Color textMuted = Color(0xFF94A3B8);
  static const Color errorRed = Color(0xFFFF4C4C);
  static const Color successGreen = Color(0xFF00FF9D);

  // Reusable Glassmorphism & Neon Effects (matching web CSS)
  static final BoxDecoration glassDecoration = BoxDecoration(
    color: Colors.white.withValues(alpha: 0.05),
    borderRadius: BorderRadius.circular(20),
    border: Border.all(color: Colors.white.withValues(alpha: 0.1), width: 1),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withValues(alpha: 0.2),
        blurRadius: 10,
        spreadRadius: 2,
      ),
    ],
  );

  static final List<BoxShadow> neonShadow = [
    BoxShadow(
      color: primaryCyan.withValues(alpha: 0.3),
      blurRadius: 15,
      spreadRadius: 2,
      offset: const Offset(0, 0),
    ),
  ];

  static ThemeData get lightTheme {
    // We are forcing a dark vibrant theme even if called lightTheme for now,
    // or we just return a dark theme configuration to replace everything globally.
    // Keeping getter name as `lightTheme` so main.dart doesn't break.
    return ThemeData(
      brightness: Brightness.dark,
      primaryColor: primaryCyan,
      scaffoldBackgroundColor: backgroundDark,
      colorScheme: const ColorScheme.dark(
        primary: primaryCyan,
        secondary: secondaryCoral,
        surface: surfaceDark,
        error: errorRed,
        onPrimary: backgroundDark,
        onSecondary: surfaceWhite,
        onSurface: textLight,
        onError: Colors.white,
      ),
      textTheme: GoogleFonts.outfitTextTheme(ThemeData.dark().textTheme).copyWith(
        displayLarge: GoogleFonts.outfit(color: textLight, fontSize: 36, fontWeight: FontWeight.w800, letterSpacing: -1.5),
        displayMedium: GoogleFonts.outfit(color: textLight, fontSize: 28, fontWeight: FontWeight.bold, letterSpacing: -1),
        titleLarge: GoogleFonts.outfit(color: textLight, fontSize: 22, fontWeight: FontWeight.w700),
        titleMedium: GoogleFonts.outfit(color: textLight, fontSize: 18, fontWeight: FontWeight.w600),
        bodyLarge: GoogleFonts.outfit(color: textLight, fontSize: 16, height: 1.5),
        bodyMedium: GoogleFonts.outfit(color: textLight, fontSize: 14, height: 1.5),
        labelLarge: GoogleFonts.outfit(color: primaryCyan, fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1),
        bodySmall: GoogleFonts.outfit(color: textMuted, fontSize: 12),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        iconTheme: const IconThemeData(color: primaryCyan),
        titleTextStyle: GoogleFonts.outfit(
          color: textLight,
          fontSize: 22,
          fontWeight: FontWeight.w800,
          letterSpacing: 0.5,
        ),
      ),
      cardTheme: CardThemeData(
        color: surfaceDark.withValues(alpha: 0.5),
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: BorderSide(color: Colors.white.withValues(alpha: 0.05), width: 1),
        ),
        margin: EdgeInsets.zero,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryCyan,
          foregroundColor: backgroundDark,
          elevation: 8,
          shadowColor: primaryCyan.withValues(alpha: 0.5),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.w800, letterSpacing: 1),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryCyan,
          side: const BorderSide(color: primaryCyan, width: 2),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, letterSpacing: 1),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: secondaryCoral,
          textStyle: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white.withValues(alpha: 0.05),
        contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
        hintStyle: GoogleFonts.outfit(color: textMuted, fontSize: 16),
        labelStyle: GoogleFonts.outfit(color: primaryCyan.withValues(alpha: 0.8), fontSize: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: primaryCyan, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: errorRed),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: errorRed, width: 2),
        ),
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: backgroundDark.withValues(alpha: 0.9),
        elevation: 0,
        selectedItemColor: primaryCyan,
        unselectedItemColor: textMuted,
        showUnselectedLabels: true,
        type: BottomNavigationBarType.fixed,
        selectedLabelStyle: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 12),
        unselectedLabelStyle: GoogleFonts.outfit(fontWeight: FontWeight.w500, fontSize: 12),
      ),
    );
  }

  // Fallback constant for internal references
  static const Color surfaceWhite = Colors.white; 
}
