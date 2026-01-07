package com.kiosk.network

import com.kiosk.network.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    // Device endpoints
    @POST("devices/register")
    suspend fun registerDevice(@Body request: DeviceRegisterRequest): Response<DeviceRegisterResponse>
    
    @GET("devices/me")
    suspend fun getDeviceInfo(): Response<DeviceResponse>
    
    @POST("devices/ping")
    suspend fun pingDevice(): Response<Unit>
    
    // Employee endpoints
    @GET("employees")
    suspend fun listEmployees(): Response<List<EmployeeResponse>>
    
    @POST("employees")
    suspend fun createEmployee(@Body request: EmployeeCreateRequest): Response<EmployeeResponse>
    
    @PUT("employees/{id}")
    suspend fun updateEmployee(@Path("id") id: String, @Body request: EmployeeUpdateRequest): Response<EmployeeResponse>
    
    @POST("employees/{id}/deactivate")
    suspend fun deactivateEmployee(@Path("id") id: String): Response<EmployeeResponse>
    
    @GET("employees/{id}/state")
    suspend fun getEmployeeState(@Path("id") id: String): Response<EmployeeStateResponse>
    
    @GET("employees/embeddings")
    suspend fun getEmbeddings(): Response<List<EmbeddingResponse>>
    
    @POST("employees/{id}/embedding")
    suspend fun storeEmbedding(@Path("id") id: String, @Body request: EmbeddingStoreRequest): Response<ApiResponse>
    
    @DELETE("employees/{id}/embedding")
    suspend fun deleteEmbedding(@Path("id") id: String): Response<Unit>
    
    // Time event endpoints
    @POST("time-events")
    suspend fun createTimeEvent(@Body request: TimeEventCreateRequest): Response<TimeEventResponse>
    
    @GET("time-events")
    suspend fun listTimeEvents(
        @Query("employee_id") employeeId: String? = null,
        @Query("start_date") startDate: String? = null,
        @Query("end_date") endDate: String? = null
    ): Response<List<TimeEventResponse>>
    
    @PUT("time-events/{id}")
    suspend fun updateTimeEvent(@Path("id") id: String, @Body request: TimeEventUpdateRequest): Response<TimeEventResponse>
    
    @DELETE("time-events/{id}")
    suspend fun invalidateTimeEvent(@Path("id") id: String): Response<Unit>
    
    @GET("time-events/clocked-in")
    suspend fun getClockedInEmployees(): Response<List<ClockedInEmployeeResponse>>
    
    // Admin endpoints
    @POST("admin/export-now")
    suspend fun exportNow(@Query("export_date") exportDate: String? = null): Response<ExportResponse>
    
    @GET("admin/stats")
    suspend fun getStats(): Response<StatsResponse>
    
    @GET("admin/clocked-in")
    suspend fun getClockedIn(): Response<List<ClockedInEmployeeResponse>>
}

