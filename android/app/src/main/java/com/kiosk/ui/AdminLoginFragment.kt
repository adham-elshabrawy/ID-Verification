package com.kiosk.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.kiosk.KioskManager
import com.kiosk.R
import com.kiosk.databinding.FragmentAdminLoginBinding
// TODO: Add bcrypt library for PIN verification

class AdminLoginFragment : Fragment() {
    
    private var _binding: FragmentAdminLoginBinding? = null
    private val binding get() = _binding!!
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentAdminLoginBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        binding.buttonLogin.setOnClickListener {
            val pin = binding.editPin.text.toString()
            // TODO: Verify PIN hash
            // For now, navigate to admin
            (requireActivity() as? MainActivity)?.let { activity ->
                activity.kioskManager.setAdminMode(true)
            }
            findNavController().navigate(R.id.adminFragment)
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

