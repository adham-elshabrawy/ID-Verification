package com.kiosk.face

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import kotlin.math.sqrt

class FaceRecognition(context: Context) {
    
    private val interpreter: Interpreter
    private val inputBuffer: ByteBuffer
    private val outputBuffer: FloatArray
    
    companion object {
        private const val MODEL_FILE = "face_model.tflite"
        private const val INPUT_SIZE = 112
        private const val EMBEDDING_SIZE = 512
        private const val PIXEL_SIZE = 3 // RGB
        private const val BATCH_SIZE = 1
        private const val BYTES_PER_CHANNEL = 4 // Float32
        
        @Volatile
        private var instance: FaceRecognition? = null
        
        fun getInstance(context: Context): FaceRecognition {
            return instance ?: synchronized(this) {
                instance ?: FaceRecognition(context).also { instance = it }
            }
        }
    }
    
    init {
        // Load TFLite model
        val modelBuffer = loadModelFile(context, MODEL_FILE)
        interpreter = Interpreter(modelBuffer)
        
        // Initialize input/output buffers
        inputBuffer = ByteBuffer.allocateDirect(
            BATCH_SIZE * INPUT_SIZE * INPUT_SIZE * PIXEL_SIZE * BYTES_PER_CHANNEL
        ).apply {
            order(ByteOrder.nativeOrder())
        }
        
        outputBuffer = FloatArray(EMBEDDING_SIZE)
    }
    
    private fun loadModelFile(context: Context, modelFile: String): MappedByteBuffer {
        val fileDescriptor = context.assets.openFd(modelFile)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }
    
    /**
     * Generate face embedding from preprocessed face image
     * Input should be 112x112 RGB image, normalized to [0, 1]
     */
    fun generateEmbedding(faceImage: Bitmap): FloatArray {
        // Resize to 112x112 if needed
        val resized = if (faceImage.width != INPUT_SIZE || faceImage.height != INPUT_SIZE) {
            Bitmap.createScaledBitmap(faceImage, INPUT_SIZE, INPUT_SIZE, true)
        } else {
            faceImage
        }
        
        // Convert bitmap to ByteBuffer (normalized to [0, 1])
        inputBuffer.rewind()
        val pixels = IntArray(INPUT_SIZE * INPUT_SIZE)
        resized.getPixels(pixels, 0, INPUT_SIZE, 0, 0, INPUT_SIZE, INPUT_SIZE)
        
        for (pixel in pixels) {
            val r = ((pixel shr 16) and 0xFF) / 255.0f
            val g = ((pixel shr 8) and 0xFF) / 255.0f
            val b = (pixel and 0xFF) / 255.0f
            
            inputBuffer.putFloat(r)
            inputBuffer.putFloat(g)
            inputBuffer.putFloat(b)
        }
        
        // Run inference
        interpreter.run(inputBuffer, outputBuffer)
        
        // Normalize embedding (L2 normalization)
        normalizeEmbedding(outputBuffer)
        
        return outputBuffer.copyOf()
    }
    
    private fun normalizeEmbedding(embedding: FloatArray) {
        var sum = 0.0f
        for (value in embedding) {
            sum += value * value
        }
        val norm = sqrt(sum)
        if (norm > 0) {
            for (i in embedding.indices) {
                embedding[i] /= norm
            }
        }
    }
}

