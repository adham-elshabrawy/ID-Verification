package com.kiosk.face

import android.content.Context
import android.util.Log
import com.kiosk.settings.DeviceSettings
import kotlin.math.sqrt

data class MatchResult(
    val employeeId: String,
    val name: String,
    val confidence: Float,
    val matched: Boolean
)

class FaceMatcher(private val context: Context) {
    
    private val faceCache = FaceCache(context)
    private val threshold = DeviceSettings.getFaceThreshold(context)
    
    /**
     * Match embedding against cached embeddings
     * Returns best match if confidence exceeds threshold
     */
    fun match(embedding: FloatArray): MatchResult? {
        val cachedEmbeddings = faceCache.loadEmbeddings()
        
        if (cachedEmbeddings.isEmpty()) {
            Log.w("FaceMatcher", "No cached embeddings available")
            return null
        }
        
        var bestMatch: CachedEmbedding? = null
        var bestScore = Float.MIN_VALUE
        
        for (cached in cachedEmbeddings) {
            val cachedEmbedding = cached.embedding.toFloatArray()
            val similarity = cosineSimilarity(embedding, cachedEmbedding)
            
            if (similarity > bestScore) {
                bestScore = similarity
                bestMatch = cached
            }
        }
        
        if (bestMatch != null && bestScore >= threshold) {
            Log.d("FaceMatcher", "Match found: ${bestMatch.employeeId} with confidence $bestScore")
            return MatchResult(
                employeeId = bestMatch.employeeId,
                name = bestMatch.name,
                confidence = bestScore,
                matched = true
            )
        }
        
        Log.d("FaceMatcher", "No match found (best score: $bestScore, threshold: $threshold)")
        return null
    }
    
    /**
     * Calculate cosine similarity between two embeddings
     */
    private fun cosineSimilarity(embedding1: FloatArray, embedding2: FloatArray): Float {
        if (embedding1.size != embedding2.size) {
            throw IllegalArgumentException("Embeddings must have same size")
        }
        
        var dotProduct = 0.0f
        var norm1 = 0.0f
        var norm2 = 0.0f
        
        for (i in embedding1.indices) {
            dotProduct += embedding1[i] * embedding2[i]
            norm1 += embedding1[i] * embedding1[i]
            norm2 += embedding2[i] * embedding2[i]
        }
        
        val denominator = sqrt(norm1) * sqrt(norm2)
        return if (denominator > 0) dotProduct / denominator else 0.0f
    }
}

