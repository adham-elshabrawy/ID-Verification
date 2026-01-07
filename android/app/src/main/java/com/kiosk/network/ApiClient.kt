package com.kiosk.network

import com.kiosk.encryption.KeystoreHelper
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {
    
    private const val BASE_URL = "http://your-backend-url/api/" // TODO: Configure
    
    private var retrofit: Retrofit? = null
    private var apiService: ApiService? = null
    
    fun getApiService(context: android.content.Context): ApiService {
        if (apiService == null) {
            apiService = getRetrofit(context).create(ApiService::class.java)
        }
        return apiService!!
    }
    
    private fun getRetrofit(context: android.content.Context): Retrofit {
        if (retrofit == null) {
            val client = OkHttpClient.Builder()
                .addInterceptor(createAuthInterceptor(context))
                .addInterceptor(createLoggingInterceptor())
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build()
            
            retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
        }
        return retrofit!!
    }
    
    private fun createAuthInterceptor(context: android.content.Context): Interceptor {
        return Interceptor { chain ->
            val request = chain.request().newBuilder()
            
            // Add API key header
            val keystoreHelper = KeystoreHelper(context)
            val apiKey = keystoreHelper.getApiKey()
            if (apiKey != null) {
                request.addHeader("X-Device-API-Key", apiKey)
            }
            
            chain.proceed(request.build())
        }
    }
    
    private fun createLoggingInterceptor(): Interceptor {
        val logging = HttpLoggingInterceptor()
        logging.level = HttpLoggingInterceptor.Level.BODY
        return logging
    }
    
    fun reset() {
        retrofit = null
        apiService = null
    }
}

