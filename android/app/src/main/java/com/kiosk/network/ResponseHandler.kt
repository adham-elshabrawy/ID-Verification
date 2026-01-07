package com.kiosk.network

import retrofit2.Response
import java.io.IOException

object ResponseHandler {
    
    fun <T> handleResponse(response: Response<T>): Result<T> {
        return try {
            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    Result.success(body)
                } else {
                    Result.failure(Exception("Response body is null"))
                }
            } else {
                val errorBody = response.errorBody()?.string()
                Result.failure(Exception("Error: ${response.code()} - $errorBody"))
            }
        } catch (e: IOException) {
            Result.failure(e)
        }
    }
    
    suspend fun <T> handleApiCall(apiCall: suspend () -> Response<T>): Result<T> {
        return try {
            val response = apiCall()
            handleResponse(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

