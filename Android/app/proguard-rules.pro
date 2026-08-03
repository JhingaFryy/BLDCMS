# Default AGP-generated file for adding project-specific ProGuard/R8 rules.
# https://developer.android.com/build/shrink-code

# Suppresses warnings from the KSP-based Hilt annotation processor.
-dontwarn com.google.devtools.ksp.**

# Retrofit, OkHttp, kotlinx.serialization and Hilt all ship their own consumer ProGuard rules
# bundled in their AARs/JARs (META-INF/proguard), which R8 applies automatically - this file only
# adds rules specific to this app's own classes.

# Keep this app's Retrofit service interfaces and their annotations.
-keep interface com.checksheet.android.data.api.** { *; }

# Keep this app's @Serializable request/response models and their generated serializers - the
# generic kotlinx.serialization consumer rule already covers any @Serializable class by wildcard,
# this just makes the intent explicit for the package Retrofit actually serializes.
-keep @kotlinx.serialization.Serializable class com.checksheet.android.data.model.** { *; }
-keepclassmembers class com.checksheet.android.data.model.** {
    *** Companion;
}
-keep,includedescriptorclasses class com.checksheet.android.data.model.**$$serializer { *; }
