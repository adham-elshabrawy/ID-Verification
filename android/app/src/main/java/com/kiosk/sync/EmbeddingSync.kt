package com.kiosk.sync

import android.content.Context
import android.util.Log
import com.kiosk.face.CachedEmbedding
import com.kiosk.face.FaceCache
import com.kiosk.network.ApiClient
import com.kiosk.network.ResponseHandler
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

object EmbeddingSync {
    
    private const val TAG = "EmbeddingSync"
    
    /**
     * Sync embeddings from server to local cache
     */
    suspend fun syncEmbeddings(context: Context): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val apiService = ApiClient.getApiService(context)
            val result = ResponseHandler.handleApiCall { apiService.getEmbeddings() }
            
            result.fold(
                onSuccess = { embeddings ->
                    val cachedEmbeddings = embeddings.map { embedding ->
                        CachedEmbedding(
                            employeeId = embedding.employeeId,
                            name = embedding.name,
                            embedding = embedding.embedding
                        )
                    }
                    
                    FaceCache(context).storeEmbeddings(cachedEmbeddings)
                    Log.d(TAG, "Synced ${cachedEmbeddings.size} embeddings")
                    Result.success(Unit)
                },
                onFailure = { error ->
                    Log.e(TAG, "Failed to sync embeddings", error)
                    Result.failure(error)
                }
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error syncing embeddings", e)
            Result.failure(e)
        }
    }
}

