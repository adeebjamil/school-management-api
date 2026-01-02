from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Vehicle, Route, TransportAssignment
from students.models import Student
from teachers.models import Teacher


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'route_number', 'route_name', 'stops', 'pickup_time', 
                  'drop_time', 'distance_km', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleSerializer(serializers.ModelSerializer):
    students_assigned = serializers.ReadOnlyField()
    route = RouteSerializer(read_only=True)
    route_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    route_data = serializers.DictField(write_only=True, required=False)
    
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_number', 'vehicle_type', 'capacity', 'driver_name', 
                  'driver_phone', 'driver_license', 'status', 'monthly_fee', 
                  'students_assigned', 'route', 'route_id', 'route_data', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        route_id = validated_data.pop('route_id', None)
        route_data = validated_data.pop('route_data', None)
        tenant = validated_data.get('tenant')
        
        # Create route if route_data is provided
        if route_data and not route_id:
            start_point = route_data.get('start_point', '')
            end_point = route_data.get('end_point', '')
            stops_list = route_data.get('stops', [])
            
            # Create route with all stops (start, middle stops, end)
            all_stops = [start_point] + stops_list + [end_point]
            
            route = Route.objects.create(
                tenant=tenant,
                route_name=f"{start_point} to {end_point}",
                stops=all_stops,
                is_active=True
            )
            route_id = route.id
        
        vehicle = Vehicle.objects.create(**validated_data)
        if route_id:
            vehicle.route_id = route_id
            vehicle.save()
        return vehicle
    
    def update(self, instance, validated_data):
        route_id = validated_data.pop('route_id', None)
        route_data = validated_data.pop('route_data', None)
        
        # Update or create route if route_data is provided
        if route_data:
            start_point = route_data.get('start_point', '')
            end_point = route_data.get('end_point', '')
            stops_list = route_data.get('stops', [])
            
            all_stops = [start_point] + stops_list + [end_point]
            
            if instance.route:
                # Update existing route
                instance.route.route_name = f"{start_point} to {end_point}"
                instance.route.stops = all_stops
                instance.route.save()
            else:
                # Create new route
                route = Route.objects.create(
                    tenant=instance.tenant,
                    route_name=f"{start_point} to {end_point}",
                    stops=all_stops,
                    is_active=True
                )
                instance.route = route
        elif route_id:
            instance.route_id = route_id
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TransportAssignmentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    class_section = serializers.SerializerMethodField()
    vehicle_details = serializers.SerializerMethodField()
    route_details = serializers.SerializerMethodField()
    
    class Meta:
        model = TransportAssignment
        fields = ['id', 'vehicle', 'route', 'user_id', 'user_name', 'user_type', 
                  'class_section', 'pickup_point', 'monthly_fee', 'status', 
                  'effective_from', 'is_active', 'vehicle_details', 'route_details',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        if hasattr(obj.user, 'user'):
            user = obj.user.user
            return user.full_name if hasattr(user, 'full_name') else f"{user.first_name} {user.last_name}"
        return str(obj.user)
    
    def get_user_type(self, obj):
        if isinstance(obj.user, Student):
            return 'student'
        elif isinstance(obj.user, Teacher):
            return 'teacher'
        return 'unknown'
    
    def get_user_id(self, obj):
        if hasattr(obj.user, 'admission_number'):
            return obj.user.admission_number
        elif hasattr(obj.user, 'employee_id'):
            return obj.user.employee_id
        return str(obj.object_id)
    
    def get_class_section(self, obj):
        if isinstance(obj.user, Student) and hasattr(obj.user, 'current_class'):
            class_obj = obj.user.current_class
            if class_obj:
                return f"{class_obj.name}-{class_obj.section}"
        return None
    
    def get_vehicle_details(self, obj):
        return {
            'id': str(obj.vehicle.id),
            'vehicle_number': obj.vehicle.vehicle_number,
            'vehicle_type': obj.vehicle.vehicle_type,
            'driver_name': obj.vehicle.driver_name,
            'driver_phone': obj.vehicle.driver_phone,
        }
    
    def get_route_details(self, obj):
        return {
            'id': str(obj.route.id),
            'route_number': obj.route.route_number,
            'route_name': obj.route.route_name,
            'pickup_time': obj.route.pickup_time.strftime('%H:%M') if obj.route.pickup_time else None,
            'drop_time': obj.route.drop_time.strftime('%H:%M') if obj.route.drop_time else None,
            'stops': obj.route.stops,
        }


class CreateTransportAssignmentSerializer(serializers.Serializer):
    vehicle_id = serializers.UUIDField()
    route_id = serializers.UUIDField()
    user_type = serializers.ChoiceField(choices=['student', 'teacher'])
    user_id = serializers.UUIDField()
    pickup_point = serializers.CharField(max_length=200)
    monthly_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    effective_from = serializers.DateField()
    status = serializers.ChoiceField(
        choices=['active', 'pending', 'inactive'],
        default='active'
    )
    
    def validate(self, data):
        # Validate vehicle
        try:
            vehicle = Vehicle.objects.get(id=data['vehicle_id'])
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError("Vehicle not found")
        
        # Validate route
        try:
            route = Route.objects.get(id=data['route_id'])
        except Route.DoesNotExist:
            raise serializers.ValidationError("Route not found")
        
        # Validate user
        user_type = data['user_type']
        user_id = data['user_id']
        
        if user_type == 'student':
            try:
                user = Student.objects.get(id=user_id)
            except Student.DoesNotExist:
                raise serializers.ValidationError("Student not found")
        elif user_type == 'teacher':
            try:
                user = Teacher.objects.get(id=user_id)
            except Teacher.DoesNotExist:
                raise serializers.ValidationError("Teacher not found")
        else:
            raise serializers.ValidationError("Invalid user type")
        
        data['vehicle'] = vehicle
        data['route'] = route
        data['user'] = user
        data['user_type_obj'] = user_type
        
        return data
    
    def create(self, validated_data):
        tenant = self.context['request'].tenant
        vehicle = validated_data['vehicle']
        route = validated_data['route']
        user = validated_data['user']
        user_type = validated_data['user_type_obj']
        
        # Get content type
        if user_type == 'student':
            content_type = ContentType.objects.get_for_model(Student)
        else:
            content_type = ContentType.objects.get_for_model(Teacher)
        
        # Create assignment
        assignment = TransportAssignment.objects.create(
            tenant=tenant,
            vehicle=vehicle,
            route=route,
            content_type=content_type,
            object_id=user.id,
            pickup_point=validated_data['pickup_point'],
            monthly_fee=validated_data['monthly_fee'],
            effective_from=validated_data['effective_from'],
            status=validated_data.get('status', 'active'),
            is_active=True
        )
        
        return assignment


class VehicleStatsSerializer(serializers.Serializer):
    total_vehicles = serializers.IntegerField()
    active_vehicles = serializers.IntegerField()
    maintenance = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_routes = serializers.IntegerField()
