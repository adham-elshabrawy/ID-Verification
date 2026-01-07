package com.kiosk.encryption

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

class KeystoreHelper(private val context: Context) {
    
    private val masterKey: MasterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val encryptedPrefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "kiosk_encrypted_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    private val keyAlias = "kiosk_api_key"
    private val embeddingKeyAlias = "kiosk_embedding_key"
    
    // API Key storage
    fun saveApiKey(apiKey: String) {
        encryptedPrefs.edit()
            .putString("api_key", apiKey)
            .apply()
    }
    
    fun getApiKey(): String? {
        return encryptedPrefs.getString("api_key", null)
    }
    
    fun hasApiKey(): Boolean {
        return getApiKey() != null
    }
    
    // Manager PIN storage (hashed)
    fun saveManagerPinHash(pinHash: String) {
        encryptedPrefs.edit()
            .putString("manager_pin_hash", pinHash)
            .apply()
    }
    
    fun getManagerPinHash(): String? {
        return encryptedPrefs.getString("manager_pin_hash", null)
    }
    
    // Embedding encryption key (for local cache)
    fun getOrCreateEmbeddingKey(): SecretKey {
        val keyStore = java.security.KeyStore.getInstance("AndroidKeyStore")
        keyStore.load(null)
        
        return if (keyStore.containsAlias(embeddingKeyAlias)) {
            val entry = keyStore.getEntry(embeddingKeyAlias, null) as java.security.KeyStore.SecretKeyEntry
            entry.secretKey
        } else {
            val keyGenerator = KeyGenerator.getInstance("AES", "AndroidKeyStore")
            val keyGenParameterSpec = android.security.keystore.KeyGenParameterSpec.Builder(
                embeddingKeyAlias,
                android.security.keystore.KeyProperties.PURPOSE_ENCRYPT or
                android.security.keystore.KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(android.security.keystore.KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(android.security.keystore.KeyProperties.ENCRYPTION_PADDING_NONE)
                .build()
            
            keyGenerator.init(keyGenParameterSpec)
            keyGenerator.generateKey()
        }
    }
    
    // Encrypt/decrypt embedding data
    fun encryptEmbedding(embedding: ByteArray): ByteArray {
        val key = getOrCreateEmbeddingKey()
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key)
        
        val iv = cipher.iv
        val encrypted = cipher.doFinal(embedding)
        
        // Prepend IV to encrypted data
        return iv + encrypted
    }
    
    fun decryptEmbedding(encryptedData: ByteArray): ByteArray {
        val key = getOrCreateEmbeddingKey()
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        
        // Extract IV (first 12 bytes for GCM)
        val iv = encryptedData.sliceArray(0 until 12)
        val encrypted = encryptedData.sliceArray(12 until encryptedData.size)
        
        val spec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.DECRYPT_MODE, key, spec)
        
        return cipher.doFinal(encrypted)
    }
}

