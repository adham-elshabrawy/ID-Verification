package com.kiosk.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.kiosk.KioskManager
import com.kiosk.MainActivity
import com.kiosk.R
import com.kiosk.databinding.FragmentAdminBinding

class AdminFragment : Fragment() {
    
    private var _binding: FragmentAdminBinding? = null
    private val binding get() = _binding!!
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAdminBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        binding.buttonExitAdmin.setOnClickListener {
            (requireActivity() as? MainActivity)?.let { activity ->
                activity.kioskManager.setAdminMode(false)
            }
            findNavController().popBackStack()
        }
        
        // TODO: Implement admin UI features
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

