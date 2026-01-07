package com.kiosk.face

import android.content.Context
import android.util.Log
import com.kiosk.encryption.KeystoreHelper
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.nio.ByteBuffer
import java.nio.ByteOrder

@Serializable
data class CachedEmbedding(
    val employeeId: String,
    val name: String,
    val embedding: List<Float>
)

class FaceCache(private val context: Context) {
    
    private val keystoreHelper = KeystoreHelper(context)
    private val cacheKey = "face_embeddings_cache"
    
    private fun getSharedPrefs() = context.getSharedPreferences("face_cache", Context.MODE_PRIVATE)
    
    /**
     * Store embeddings in encrypted cache
     */
    fun storeEmbeddings(embeddings: List<CachedEmbedding>) {
        try {
            val json = Json.encodeToString(embeddings)
            val jsonBytes = json.toByteArray(Charsets.UTF_8)
            val encrypted = keystoreHelper.encryptEmbedding(jsonBytes)
            
            getSharedPrefs().edit()
                .putString(cacheKey, android.util.Base64.encodeToString(encrypted, android.util.Base64.DEFAULT))
                .apply()
            
            Log.d("FaceCache", "Stored ${embeddings.size} embeddings")
        } catch (e: Exception) {
            Log.e("FaceCache", "Error storing embeddings", e)
        }
    }
    
    /**
     * Load embeddings from encrypted cache
     */
    fun loadEmbeddings(): List<CachedEmbedding> {
        return try {
            val encryptedB64 = getSharedPrefs().getString(cacheKey, null) ?: return emptyList()
            val encrypted = android.util.Base64.decode(encryptedB64, android.util.Base64.DEFAULT)
            val decrypted = keystoreHelper.decryptEmbedding(encrypted)
            val json = String(decrypted, Charsets.UTF_8)
            Json.decodeFromString<List<CachedEmbedding>>(json)
        } catch (e: Exception) {
            Log.e("FaceCache", "Error loading embeddings", e)
            emptyList()
        }
    }
    
    /**
     * Clear cache
     */
    fun clearCache() {
        getSharedPrefs().edit().remove(cacheKey).apply()
    }
    
    /**
     * Get embedding for specific employee
     */
    fun getEmbedding(employeeId: String): FloatArray? {
        val embeddings = loadEmbeddings()
        val cached = embeddings.find { it.employeeId == employeeId }
        return cached?.embedding?.toFloatArray()
    }
}

