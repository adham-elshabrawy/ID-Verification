package com.kiosk.database.dao

import androidx.room.*
import com.kiosk.database.entities.TimeEventEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface TimeEventDao {
    
    @Query("SELECT * FROM time_events WHERE synced = 0 ORDER BY createdAt ASC")
    fun getUnsyncedEvents(): Flow<List<TimeEventEntity>>
    
    @Query("SELECT * FROM time_events WHERE synced = 0 ORDER BY createdAt ASC")
    suspend fun getUnsyncedEventsList(): List<TimeEventEntity>
    
    @Insert
    suspend fun insert(event: TimeEventEntity)
    
    @Update
    suspend fun update(event: TimeEventEntity)
    
    @Query("UPDATE time_events SET synced = 1 WHERE id = :id")
    suspend fun markSynced(id: String)
    
    @Delete
    suspend fun delete(event: TimeEventEntity)
}

