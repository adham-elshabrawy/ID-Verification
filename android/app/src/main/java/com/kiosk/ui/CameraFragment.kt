package com.kiosk.ui

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.kiosk.R
import com.kiosk.databinding.FragmentCameraBinding
import com.kiosk.face.FaceRecognition
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class CameraFragment : Fragment() {
    
    private var _binding: FragmentCameraBinding? = null
    private val binding get() = _binding!!
    private val args: CameraFragmentArgs by navArgs()
    
    private var imageCapture: ImageCapture? = null
    private var cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()
    private val faceRecognition = FaceRecognition.getInstance(requireContext())
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCameraBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        if (allPermissionsGranted()) {
            startCamera()
        } else {
            requestPermissions(arrayOf(Manifest.permission.CAMERA), REQUEST_CODE_PERMISSIONS)
        }
        
        binding.buttonCapture.setOnClickListener {
            captureImage()
        }
    }
    
    private fun allPermissionsGranted() = ContextCompat.checkSelfPermission(
        requireContext(), Manifest.permission.CAMERA
    ) == PackageManager.PERMISSION_GRANTED
    
    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(requireContext())
        
        cameraProviderFuture.addListener({
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()
            
            val preview = Preview.Builder()
                .build()
                .also {
                    it.setSurfaceProvider(binding.viewFinder.surfaceProvider)
                }
            
            imageCapture = ImageCapture.Builder().build()
            
            val cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA
            
            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    this, cameraSelector, preview, imageCapture
                )
            } catch (exc: Exception) {
                // Handle error
            }
        }, ContextCompat.getMainExecutor(requireContext()))
    }
    
    private fun captureImage() {
        val imageCapture = imageCapture ?: return
        
        val outputFileOptions = ImageCapture.OutputFileOptions.Builder(
            requireContext().cacheDir.resolve("temp_face.jpg")
        ).build()
        
        imageCapture.takePicture(
            outputFileOptions,
            cameraExecutor,
            object : ImageCapture.OnImageSavedCallback {
                override fun onError(exception: ImageCaptureException) {
                    // Handle error
                    findNavController().navigate(R.id.errorFragment)
                }
                
                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                    // Process captured image
                    processImage(output.savedUri?.path ?: return)
                }
            }
        )
    }
    
    private fun processImage(imagePath: String) {
        // Load bitmap and process
        // For now, navigate to processing/confirm screen
        // In real implementation, do face detection and recognition here
        val action = CameraFragmentDirections.actionCameraFragmentToConfirmFragment(
            eventType = args.eventType,
            employeeId = "EMP001", // Placeholder
            employeeName = "John Doe", // Placeholder
            confidence = 0.85f
        )
        findNavController().navigate(action)
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (allPermissionsGranted()) {
                startCamera()
            } else {
                // Permission denied
                findNavController().popBackStack()
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
    
    companion object {
        private const val REQUEST_CODE_PERMISSIONS = 10
    }
}

